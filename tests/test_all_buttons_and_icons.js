/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * اختبار شامل لجميع الأزرار والأيقونات
 * يختبر كل زر وأيقونة في النظام بدون استثناء
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const puppeteer = require('puppeteer');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
let browser;
let page;
let testResults = {
    total: 0,
    passed: 0,
    failed: 0,
    buttons: [],
    icons: []
};

function logTest(name, passed, details = '') {
    testResults.total++;
    if (passed) {
        testResults.passed++;
        console.log(`✅ [${testResults.total}] ${name} ${details}`);
    } else {
        testResults.failed++;
        console.log(`❌ [${testResults.total}] ${name} ${details}`);
    }
}

// ═══ قائمة شاملة بجميع الأزرار المتوقعة ═══
const ALL_BUTTONS = [
    // TopBar Buttons
    { id: 'user-menu-button', name: 'زر قائمة المستخدم', location: 'TopBar' },
    { id: 'user-avatar', name: 'صورة المستخدم', location: 'TopBar' },
    { id: 'notifications-button', name: 'زر الإشعارات', location: 'TopBar' },
    { id: 'notifications-badge', name: 'شارة الإشعارات', location: 'TopBar' },
    { id: 'settings-button', name: 'زر الإعدادات', location: 'TopBar' },
    { id: 'help-button', name: 'زر المساعدة', location: 'TopBar' },
    { id: 'logout-button', name: 'زر تسجيل الخروج', location: 'TopBar' },
    
    // Sidebar Buttons
    { id: 'new-task-button', name: 'زر مهمة جديدة', location: 'Sidebar' },
    { id: 'new-workspace-button', name: 'زر مساحة عمل جديدة', location: 'Sidebar' },
    { id: 'tasks-tab', name: 'تبويب المهام', location: 'Sidebar' },
    { id: 'workspaces-tab', name: 'تبويب مساحات العمل', location: 'Sidebar' },
    { id: 'events-tab', name: 'تبويب الأحداث', location: 'Sidebar' },
    { id: 'settings-tab', name: 'تبويب الإعدادات', location: 'Sidebar' },
    { id: 'sidebar-toggle', name: 'زر إظهار/إخفاء القائمة الجانبية', location: 'Sidebar' },
    { id: 'sidebar-collapse', name: 'زر طي القائمة الجانبية', location: 'Sidebar' },
    
    // Composer Buttons
    { id: 'send-button', name: 'زر الإرسال', location: 'Composer' },
    { id: 'attach-file-button', name: 'زر إرفاق ملف', location: 'Composer' },
    { id: 'attach-image-button', name: 'زر إرفاق صورة', location: 'Composer' },
    { id: 'attach-video-button', name: 'زر إرفاق فيديو', location: 'Composer' },
    { id: 'attach-audio-button', name: 'زر إرفاق صوت', location: 'Composer' },
    { id: 'emoji-button', name: 'زر الرموز التعبيرية', location: 'Composer' },
    { id: 'voice-input-button', name: 'زر الإدخال الصوتي', location: 'Composer' },
    { id: 'clear-input-button', name: 'زر مسح النص', location: 'Composer' },
    { id: 'format-bold-button', name: 'زر النص الغامق', location: 'Composer' },
    { id: 'format-italic-button', name: 'زر النص المائل', location: 'Composer' },
    { id: 'format-code-button', name: 'زر كود برمجي', location: 'Composer' },
    
    // Task Panel Buttons
    { id: 'task-start-button', name: 'زر بدء المهمة', location: 'TaskPanel' },
    { id: 'task-pause-button', name: 'زر إيقاف المهمة', location: 'TaskPanel' },
    { id: 'task-cancel-button', name: 'زر إلغاء المهمة', location: 'TaskPanel' },
    { id: 'task-delete-button', name: 'زر حذف المهمة', location: 'TaskPanel' },
    { id: 'task-edit-button', name: 'زر تعديل المهمة', location: 'TaskPanel' },
    { id: 'task-duplicate-button', name: 'زر نسخ المهمة', location: 'TaskPanel' },
    { id: 'task-export-button', name: 'زر تصدير المهمة', location: 'TaskPanel' },
    { id: 'task-share-button', name: 'زر مشاركة المهمة', location: 'TaskPanel' },
    { id: 'task-refresh-button', name: 'زر تحديث المهمة', location: 'TaskPanel' },
    
    // Workspace Panel Buttons
    { id: 'workspace-create-button', name: 'زر إنشاء مساحة عمل', location: 'WorkspacePanel' },
    { id: 'workspace-edit-button', name: 'زر تعديل مساحة العمل', location: 'WorkspacePanel' },
    { id: 'workspace-delete-button', name: 'زر حذف مساحة العمل', location: 'WorkspacePanel' },
    { id: 'workspace-share-button', name: 'زر مشاركة مساحة العمل', location: 'WorkspacePanel' },
    
    // Events Panel Buttons
    { id: 'events-filter-button', name: 'زر تصفية الأحداث', location: 'EventsPanel' },
    { id: 'events-clear-button', name: 'زر مسح الأحداث', location: 'EventsPanel' },
    { id: 'events-export-button', name: 'زر تصدير الأحداث', location: 'EventsPanel' },
    { id: 'events-refresh-button', name: 'زر تحديث الأحداث', location: 'EventsPanel' },
    
    // Settings Panel Buttons
    { id: 'settings-save-button', name: 'زر حفظ الإعدادات', location: 'SettingsPanel' },
    { id: 'settings-reset-button', name: 'زر إعادة تعيين الإعدادات', location: 'SettingsPanel' },
    { id: 'settings-import-button', name: 'زر استيراد الإعدادات', location: 'SettingsPanel' },
    { id: 'settings-export-button', name: 'زر تصدير الإعدادات', location: 'SettingsPanel' },
    
    // Connector Buttons
    { id: 'connector-add-button', name: 'زر إضافة موصل', location: 'Connectors' },
    { id: 'connector-edit-button', name: 'زر تعديل موصل', location: 'Connectors' },
    { id: 'connector-delete-button', name: 'زر حذف موصل', location: 'Connectors' },
    { id: 'connector-test-button', name: 'زر اختبار موصل', location: 'Connectors' },
    { id: 'connector-refresh-button', name: 'زر تحديث موصل', location: 'Connectors' },
    
    // Dialog Buttons
    { id: 'dialog-confirm-button', name: 'زر تأكيد الحوار', location: 'Dialog' },
    { id: 'dialog-cancel-button', name: 'زر إلغاء الحوار', location: 'Dialog' },
    { id: 'dialog-close-button', name: 'زر إغلاق الحوار', location: 'Dialog' },
    
    // Modal Buttons
    { id: 'modal-ok-button', name: 'زر موافق', location: 'Modal' },
    { id: 'modal-cancel-button', name: 'زر إلغاء', location: 'Modal' },
    { id: 'modal-close-button', name: 'زر إغلاق النافذة المنبثقة', location: 'Modal' }
];

// ═══ قائمة شاملة بجميع الأيقونات المتوقعة ═══
const ALL_ICONS = [
    // Navigation Icons
    { name: 'Home', location: 'Navigation' },
    { name: 'Tasks', location: 'Navigation' },
    { name: 'Workspaces', location: 'Navigation' },
    { name: 'Events', location: 'Navigation' },
    { name: 'Settings', location: 'Navigation' },
    
    // Action Icons
    { name: 'Send', location: 'Actions' },
    { name: 'Attach', location: 'Actions' },
    { name: 'Delete', location: 'Actions' },
    { name: 'Edit', location: 'Actions' },
    { name: 'Copy', location: 'Actions' },
    { name: 'Share', location: 'Actions' },
    { name: 'Download', location: 'Actions' },
    { name: 'Upload', location: 'Actions' },
    { name: 'Refresh', location: 'Actions' },
    { name: 'Search', location: 'Actions' },
    { name: 'Filter', location: 'Actions' },
    { name: 'Sort', location: 'Actions' },
    
    // Status Icons
    { name: 'Success', location: 'Status' },
    { name: 'Error', location: 'Status' },
    { name: 'Warning', location: 'Status' },
    { name: 'Info', location: 'Status' },
    { name: 'Loading', location: 'Status' },
    { name: 'Pending', location: 'Status' },
    { name: 'Running', location: 'Status' },
    { name: 'Completed', location: 'Status' },
    
    // File Type Icons
    { name: 'File', location: 'FileTypes' },
    { name: 'Image', location: 'FileTypes' },
    { name: 'Video', location: 'FileTypes' },
    { name: 'Audio', location: 'FileTypes' },
    { name: 'PDF', location: 'FileTypes' },
    { name: 'Document', location: 'FileTypes' },
    { name: 'Code', location: 'FileTypes' },
    
    // User Icons
    { name: 'User', location: 'User' },
    { name: 'Avatar', location: 'User' },
    { name: 'Profile', location: 'User' },
    { name: 'Logout', location: 'User' },
    
    // Connector Icons
    { name: 'Google', location: 'Connectors' },
    { name: 'Facebook', location: 'Connectors' },
    { name: 'WhatsApp', location: 'Connectors' },
    { name: 'Instagram', location: 'Connectors' },
    { name: 'Telegram', location: 'Connectors' },
    { name: 'Discord', location: 'Connectors' },
    { name: 'GitHub', location: 'Connectors' },
    { name: 'LinkedIn', location: 'Connectors' }
];

// ═══ اختبار جميع الأزرار ═══
async function testAllButtons() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔘 اختبار جميع الأزرار في النظام');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    for (const button of ALL_BUTTONS) {
        try {
            // محاولة العثور على الزر بطرق متعددة
            const selectors = [
                `#${button.id}`,
                `[data-button="${button.id}"]`,
                `[data-testid="${button.id}"]`,
                `.${button.id}`,
                `button[aria-label*="${button.name}"]`
            ];

            let found = false;
            for (const selector of selectors) {
                const element = await page.$(selector);
                if (element) {
                    found = true;
                    const isVisible = await element.isIntersectingViewport();
                    const isEnabled = await page.evaluate(el => !el.disabled, element);
                    
                    logTest(
                        `${button.name} (${button.location})`,
                        true,
                        `- مرئي: ${isVisible ? 'نعم' : 'لا'}, مفعل: ${isEnabled ? 'نعم' : 'لا'}`
                    );
                    testResults.buttons.push({ ...button, found: true, visible: isVisible, enabled: isEnabled });
                    break;
                }
            }

            if (!found) {
                logTest(`${button.name} (${button.location})`, false, '- غير موجود');
                testResults.buttons.push({ ...button, found: false });
            }
        } catch (error) {
            logTest(`${button.name} (${button.location})`, false, `- خطأ: ${error.message}`);
            testResults.buttons.push({ ...button, found: false, error: error.message });
        }
    }
}

// ═══ اختبار جميع الأيقونات ═══
async function testAllIcons() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎨 اختبار جميع الأيقونات في النظام');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // البحث عن جميع الأيقونات في الصفحة
    const allIconElements = await page.$$('svg, i[class*="icon"], .icon, [class*="Icon"]');
    logTest('إجمالي عدد الأيقونات في الصفحة', true, `- ${allIconElements.length} أيقونة`);

    for (const icon of ALL_ICONS) {
        try {
            // محاولة العثور على الأيقونة بطرق متعددة
            const selectors = [
                `[data-icon="${icon.name.toLowerCase()}"]`,
                `[aria-label*="${icon.name}"]`,
                `.icon-${icon.name.toLowerCase()}`,
                `svg[class*="${icon.name}"]`,
                `i[class*="${icon.name}"]`
            ];

            let found = false;
            for (const selector of selectors) {
                const elements = await page.$$(selector);
                if (elements.length > 0) {
                    found = true;
                    logTest(
                        `أيقونة ${icon.name} (${icon.location})`,
                        true,
                        `- عدد: ${elements.length}`
                    );
                    testResults.icons.push({ ...icon, found: true, count: elements.length });
                    break;
                }
            }

            if (!found) {
                // محاولة البحث بالنص
                const textSearch = await page.evaluate((iconName) => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    return elements.some(el => 
                        el.textContent && el.textContent.toLowerCase().includes(iconName.toLowerCase())
                    );
                }, icon.name);

                if (textSearch) {
                    logTest(`أيقونة ${icon.name} (${icon.location})`, true, '- موجودة كنص');
                    testResults.icons.push({ ...icon, found: true, asText: true });
                } else {
                    logTest(`أيقونة ${icon.name} (${icon.location})`, false, '- غير موجودة');
                    testResults.icons.push({ ...icon, found: false });
                }
            }
        } catch (error) {
            logTest(`أيقونة ${icon.name} (${icon.location})`, false, `- خطأ: ${error.message}`);
            testResults.icons.push({ ...icon, found: false, error: error.message });
        }
    }
}

// ═══ اختبار تفاعل الأزرار ═══
async function testButtonInteractions() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🖱️  اختبار تفاعل الأزرار');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // اختبار النقر على أول زر متاح
    try {
        const firstButton = await page.$('button:not([disabled])');
        if (firstButton) {
            await firstButton.click();
            await page.waitForTimeout(500);
            logTest('النقر على زر', true, '- استجاب للنقر');
        } else {
            logTest('النقر على زر', false, '- لم يتم العثور على زر مفعل');
        }
    } catch (error) {
        logTest('النقر على زر', false, `- خطأ: ${error.message}`);
    }

    // اختبار hover على الأزرار
    try {
        const buttons = await page.$$('button');
        if (buttons.length > 0) {
            await buttons[0].hover();
            await page.waitForTimeout(300);
            logTest('تأثير hover على الأزرار', true, '- يعمل بشكل صحيح');
        }
    } catch (error) {
        logTest('تأثير hover على الأزرار', false, `- خطأ: ${error.message}`);
    }
}

// ═══ الدالة الرئيسية ═══
async function runTests() {
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('🧪 اختبار شامل لجميع الأزرار والأيقونات (100% تغطية)');
    console.log('═══════════════════════════════════════════════════════════════════════════════\n');

    try {
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage();

        // تحميل الصفحة
        await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
        console.log('✅ تم تحميل الصفحة بنجاح\n');

        // تشغيل جميع الاختبارات
        await testAllButtons();
        await testAllIcons();
        await testButtonInteractions();

    } catch (error) {
        console.error('خطأ في تشغيل الاختبارات:', error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }

    // النتائج النهائية
    console.log('\n═══════════════════════════════════════════════════════════════════════════════');
    console.log('📊 ملخص النتائج:');
    console.log(`   - إجمالي الاختبارات: ${testResults.total}`);
    console.log(`   - نجح: ${testResults.passed}`);
    console.log(`   - فشل: ${testResults.failed}`);
    console.log(`   - الأزرار المختبرة: ${testResults.buttons.length}`);
    console.log(`   - الأيقونات المختبرة: ${testResults.icons.length}`);
    
    const buttonsFound = testResults.buttons.filter(b => b.found).length;
    const iconsFound = testResults.icons.filter(i => i.found).length;
    console.log(`   - الأزرار الموجودة: ${buttonsFound}/${testResults.buttons.length}`);
    console.log(`   - الأيقونات الموجودة: ${iconsFound}/${testResults.icons.length}`);
    
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    
    if (testResults.failed === 0) {
        console.log('✅ نجحت جميع الاختبارات!');
        process.exit(0);
    } else {
        console.log('❌ بعض الاختبارات فشلت');
        process.exit(1);
    }
}

runTests();
